/* Input driver defined by defs/JK08A.rpm-remaining-inhibit.toml. */
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
#include "rpm-remaining-inhibit-path-cases.h"
_Static_assert(sizeof(void *)==4U,"SH-2E pointer ABI");
_Static_assert(sizeof(struct context)==80U,"complete incoming context");
_Static_assert(offsetof(struct context,fifth)==76U,"existing observer stack argument");
_Static_assert(sizeof(struct observation)==572U,"complete observer result");
_Static_assert(offsetof(struct observation,frame_before)==184U,"complete incoming frame");
_Static_assert(offsetof(struct observation,frame_after)==376U,"complete terminal frame");
_Static_assert(offsetof(struct observation,sr_before)==568U,"complete prepared SR");
extern void stock_invoke_ignition_consumer(uint32_t,const struct context *,struct observation *);
static uint8_t memory_before[RAM_SIZE],calibration_before[RPM_REMAINING_CALIBRATION_SIZE];
static uint8_t bound_before[RPM_REMAINING_BOUND_SIZE];
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
    if((input->entry!=0x4edc6U && input->entry!=0x4ede4U && input->entry!=0x4ee00U) || input->kind>=3U || input->stationary_flags>0xffU || input->vehicle_state>0xffU || input->stationary_gate>0xffU || input->source_flags>0xffU || input->readiness_timer>0xffU || input->qualifier>0xffU || input->bypass_flags>0xffU || input->rpm50>0xffU || input->thermal_flags>0xffU || input->thermal_gate>0xffU || input->temperature_gate>0xffU || input->diagnostic_flags>0xffU || input->diagnostic_count>0xffU || input->sustained_flags>0xffU || input->rpm25>0xffU || input->ceiling_flags>0xffU || input->request>0xffU || input->can_flags>0xffU || input->can_status>0xffU || input->limit_status>0xffU || input->rpm16>0xffffU || input->readiness>0xffffU || input->exposure>0xffffU || input->stationary_cut>0xffU || input->stationary_restore>0xffU || input->ready_threshold>0xffffU || input->qualifier_floor>0xffU || input->diagnostic_mode>0xffU || input->temperature_threshold>0xffU || input->thermal_hysteresis>0xffU || input->thermal_rpm_threshold>0xffU || input->disable_mask>0xffU || input->exposure_base>0xffffU || input->sustained_cut>0xffU || input->sustained_restore>0xffU || input->exposure_factor>0xffU || input->ceiling_hysteresis>0xffU || input->ceiling_floor>0xffU || input->variant>0x1U)return 0;
    memset((void *)(uintptr_t)RAM_BASE,0xa5,RAM_SIZE);
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x247fU)=(uint8_t)input->stationary_flags;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x110eU)=(uint8_t)input->vehicle_state;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x244fU)=(uint8_t)input->stationary_gate;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x2458U)=(uint8_t)input->source_flags;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x258aU)=(uint8_t)input->readiness_timer;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1071U)=(uint8_t)input->qualifier;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x245dU)=(uint8_t)input->bypass_flags;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x11aeU)=(uint8_t)input->rpm50;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x41f2U)=(uint8_t)input->thermal_flags;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x41eeU)=(uint8_t)input->thermal_gate;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x4209U)=(uint8_t)input->temperature_gate;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x5720U)=(uint8_t)input->diagnostic_flags;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x571eU)=(uint8_t)input->diagnostic_count;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x247cU)=(uint8_t)input->sustained_flags;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x11b3U)=(uint8_t)input->rpm25;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x249cU)=(uint8_t)input->ceiling_flags;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x2714U)=(uint8_t)input->request;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x2488U)=(uint8_t)input->can_flags;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x4189U)=(uint8_t)input->can_status;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x4250U)=(uint8_t)input->limit_status;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x11bcU)=(uint16_t)input->rpm16;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x16a6U)=(uint16_t)input->readiness;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x1932U)=(uint16_t)input->exposure;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x4184U)=(uint8_t)0xc0U;
    for(index=0;index<ARRAY_SIZE(rpm_remaining_controlled);++index){
        memcpy((void *)(uintptr_t)rpm_remaining_controlled[index].address,input->calibration+offset,
            rpm_remaining_controlled[index].size);
        offset+=rpm_remaining_controlled[index].size;
    }
    if(offset!=RPM_REMAINING_CALIBRATION_SIZE)return 0;
    return 1;
}
int main(void)
{
    unsigned long index;
    for(index=0;index<ARRAY_SIZE(rpm_remaining_cases);++index){
        const struct path_case *input=&rpm_remaining_cases[index];
        struct context before,context=input->context;struct observation out;
        if(!prepare(input))return 1;
        memcpy(&before,&context,sizeof(before));memset(&out,0xa6,sizeof(out));
        memcpy(memory_before,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
        snapshot(calibration_before,rpm_remaining_controlled,ARRAY_SIZE(rpm_remaining_controlled));
        snapshot(bound_before,rpm_remaining_bound,ARRAY_SIZE(rpm_remaining_bound));
        stock_invoke_ignition_consumer(input->entry,&context,&out);
        printf("kb-rpm-remaining-inhibit-observation {\"schema\":1,\"index\":%lu,\"kind\":%lu,\"entry\":%lu,\"context\":\"",
            index,(unsigned long)input->kind,(unsigned long)input->entry);
        hex(&before,sizeof(before));printf("\",\"context_after\":\"");hex(&context,sizeof(context));
        printf("\",\"observation\":\"");hex(&out,sizeof(out));
        printf("\",\"ram_before\":\"");rle(memory_before,RAM_SIZE);
        printf("\",\"ram_after\":\"");rle((const uint8_t *)(uintptr_t)RAM_BASE,RAM_SIZE);
        printf("\",\"calibration_before\":\"");hex(calibration_before,sizeof(calibration_before));
        printf("\",\"calibration_after\":\"");print_spans(rpm_remaining_controlled,ARRAY_SIZE(rpm_remaining_controlled));
        printf("\",\"bound_before\":\"");hex(bound_before,sizeof(bound_before));
        printf("\",\"bound_after\":\"");print_spans(rpm_remaining_bound,ARRAY_SIZE(rpm_remaining_bound));
        printf("\"}\n");
    }
    printf("VQ_SH_ELF_RPM_REMAINING_INHIBIT status=PASS region=%s cases=%lu\n",RPM_REMAINING_REGION,index);
    return 0;
}
