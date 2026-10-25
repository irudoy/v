/* Input driver defined by defs/JK08A.rpm-state-withdrawal-paths.toml. */
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
#include "rpm-state-withdrawal-cases.h"
_Static_assert(sizeof(void *)==4U,"SH-2E pointer ABI");
_Static_assert(sizeof(struct context)==80U,"complete incoming context");
_Static_assert(offsetof(struct context,fifth)==76U,"existing observer stack argument");
_Static_assert(sizeof(struct observation)==572U,"complete observer result");
_Static_assert(offsetof(struct observation,frame_before)==184U,"complete incoming frame");
_Static_assert(offsetof(struct observation,frame_after)==376U,"complete terminal frame");
_Static_assert(offsetof(struct observation,sr_before)==568U,"complete prepared SR");
extern void stock_invoke_ignition_consumer(uint32_t,const struct context *,struct observation *);
static uint8_t memory_before[RAM_SIZE],calibration_before[RPM_STATE_WITHDRAWAL_CALIBRATION_SIZE];
static uint8_t bound_before[RPM_STATE_WITHDRAWAL_BOUND_SIZE];
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
    if((input->entry!=0x4f7e0U && input->entry!=0x4f9c4U) || input->kind>=2U || input->exposure>0xffffU || input->source_flags>0xffU || input->reset_flags>0xffU || input->limit_flags>0xffU || input->configuration_state>0xffU || input->mode_flags>0xffU || input->boundary_state>0xffU || input->rpm>0xffU || input->transition_latch>0xffU || input->transition_clock>0xffU || input->edge_flags>0xffU || input->transition_flags>0xffU || input->warm_state>0xffU || input->disable_mask>0xffU || input->exposure_base>0xffffU || input->boundary_threshold>0xffU || input->upper_rpm>0xffU || input->lower_rpm>0xffU || input->exposure_step>0xffU || input->gate_configuration>0xffU || input->restore_rpm>0xffU || input->restore_count>0xffU || input->entry_rpm>0xffU || input->warm_threshold>0xffU || input->entry_boundary>0xffU || input->entry_count>0xffU || input->variant>0xffU || input->initial_sr>0x3ffU)return 0;
    memset((void *)(uintptr_t)RAM_BASE,0xa5,RAM_SIZE);
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x1932U)=(uint16_t)input->exposure;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x2458U)=(uint8_t)input->source_flags;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x244fU)=(uint8_t)input->reset_flags;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x4250U)=(uint8_t)input->limit_flags;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x24cfU)=(uint8_t)input->configuration_state;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x41d4U)=(uint8_t)input->mode_flags;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x110eU)=(uint8_t)input->boundary_state;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x11b3U)=(uint8_t)input->rpm;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x2497U)=(uint8_t)input->transition_latch;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1690U)=(uint8_t)input->transition_clock;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x2453U)=(uint8_t)input->edge_flags;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x245dU)=(uint8_t)input->transition_flags;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1071U)=(uint8_t)input->warm_state;
    for(index=0;index<ARRAY_SIZE(rpm_state_withdrawal_controlled);++index){
        memcpy((void *)(uintptr_t)rpm_state_withdrawal_controlled[index].address,input->calibration+offset,
            rpm_state_withdrawal_controlled[index].size);
        offset+=rpm_state_withdrawal_controlled[index].size;
    }
    if(offset!=RPM_STATE_WITHDRAWAL_CALIBRATION_SIZE)return 0;
    return 1;
}
int main(void)
{
    unsigned long index;
    for(index=0;index<ARRAY_SIZE(rpm_state_withdrawal_cases);++index){
        const struct path_case *input=&rpm_state_withdrawal_cases[index];
        struct context before,context=input->context;struct observation out;
        if(!prepare(input))return 1;
        memcpy(&before,&context,sizeof(before));memset(&out,0xa6,sizeof(out));
        memcpy(memory_before,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
        snapshot(calibration_before,rpm_state_withdrawal_controlled,ARRAY_SIZE(rpm_state_withdrawal_controlled));
        snapshot(bound_before,rpm_state_withdrawal_bound,ARRAY_SIZE(rpm_state_withdrawal_bound));
        stock_invoke_ignition_consumer(input->entry,&context,&out);
        printf("kb-rpm-state-withdrawal-observation {\"schema\":1,\"index\":%lu,\"kind\":%lu,\"entry\":%lu,\"context\":\"",
            index,(unsigned long)input->kind,(unsigned long)input->entry);
        hex(&before,sizeof(before));printf("\",\"context_after\":\"");hex(&context,sizeof(context));
        printf("\",\"observation\":\"");hex(&out,sizeof(out));
        printf("\",\"ram_before\":\"");rle(memory_before,RAM_SIZE);
        printf("\",\"ram_after\":\"");rle((const uint8_t *)(uintptr_t)RAM_BASE,RAM_SIZE);
        printf("\",\"calibration_before\":\"");hex(calibration_before,sizeof(calibration_before));
        printf("\",\"calibration_after\":\"");print_spans(rpm_state_withdrawal_controlled,ARRAY_SIZE(rpm_state_withdrawal_controlled));
        printf("\",\"bound_before\":\"");hex(bound_before,sizeof(bound_before));
        printf("\",\"bound_after\":\"");print_spans(rpm_state_withdrawal_bound,ARRAY_SIZE(rpm_state_withdrawal_bound));
        printf("\"}\n");
    }
    printf("VQ_SH_ELF_RPM_STATE_WITHDRAWAL status=PASS region=%s cases=%lu\n",RPM_STATE_WITHDRAWAL_REGION,index);
    return 0;
}
