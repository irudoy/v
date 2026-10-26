/* Input driver defined by defs/JK08A.diagnostic-record-composite-gate-paths.toml. */
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
#include "diagnostic-record-composite-gate-cases.h"
_Static_assert(sizeof(void *)==4U,"SH-2E pointer ABI");
_Static_assert(sizeof(struct context)==80U,"complete incoming context");
_Static_assert(offsetof(struct context,fifth)==76U,"existing observer stack argument");
_Static_assert(sizeof(struct observation)==572U,"complete observer result");
_Static_assert(offsetof(struct observation,frame_before)==184U,"complete incoming frame");
_Static_assert(offsetof(struct observation,frame_after)==376U,"complete terminal frame");
_Static_assert(offsetof(struct observation,sr_before)==568U,"complete prepared SR");
extern void stock_invoke_ignition_consumer(uint32_t,const struct context *,struct observation *);
static uint8_t memory_before[RAM_SIZE],calibration_before[DIAGNOSTIC_RECORD_COMPOSITE_GATE_CALIBRATION_SIZE];
static uint8_t bound_before[DIAGNOSTIC_RECORD_COMPOSITE_GATE_BOUND_SIZE];
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
    
    if((input->entry!=0x25a12U) || input->kind>=1U || input->record_014_0>0xffU || input->record_014_1>0xffU || input->record_014_2>0xffU || input->record_047_0>0xffU || input->record_047_1>0xffU || input->record_047_2>0xffU || input->record_048_0>0xffU || input->record_048_1>0xffU || input->record_048_2>0xffU || input->record_049_0>0xffU || input->record_049_1>0xffU || input->record_049_2>0xffU || input->record_04a_0>0xffU || input->record_04a_1>0xffU || input->record_04a_2>0xffU || input->record_04b_0>0xffU || input->record_04b_1>0xffU || input->record_04b_2>0xffU || input->record_04c_0>0xffU || input->record_04c_1>0xffU || input->record_04c_2>0xffU || input->record_08a_0>0xffU || input->record_08a_1>0xffU || input->record_08a_2>0xffU || input->record_08b_0>0xffU || input->record_08b_1>0xffU || input->record_08b_2>0xffU || input->record_08c_0>0xffU || input->record_08c_1>0xffU || input->record_08c_2>0xffU || input->variant>0xffU || input->initial_sr>0x3ffU)return 0;
    memset((void *)(uintptr_t)RAM_BASE,0xa5,RAM_SIZE);
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x5754U)=(uint8_t)input->record_014_0;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x5755U)=(uint8_t)input->record_014_1;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x5756U)=(uint8_t)input->record_014_2;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x57edU)=(uint8_t)input->record_047_0;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x57eeU)=(uint8_t)input->record_047_1;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x57efU)=(uint8_t)input->record_047_2;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x57f0U)=(uint8_t)input->record_048_0;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x57f1U)=(uint8_t)input->record_048_1;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x57f2U)=(uint8_t)input->record_048_2;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x57f3U)=(uint8_t)input->record_049_0;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x57f4U)=(uint8_t)input->record_049_1;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x57f5U)=(uint8_t)input->record_049_2;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x57f6U)=(uint8_t)input->record_04a_0;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x57f7U)=(uint8_t)input->record_04a_1;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x57f8U)=(uint8_t)input->record_04a_2;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x57f9U)=(uint8_t)input->record_04b_0;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x57faU)=(uint8_t)input->record_04b_1;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x57fbU)=(uint8_t)input->record_04b_2;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x57fcU)=(uint8_t)input->record_04c_0;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x57fdU)=(uint8_t)input->record_04c_1;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x57feU)=(uint8_t)input->record_04c_2;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x58b6U)=(uint8_t)input->record_08a_0;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x58b7U)=(uint8_t)input->record_08a_1;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x58b8U)=(uint8_t)input->record_08a_2;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x58b9U)=(uint8_t)input->record_08b_0;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x58baU)=(uint8_t)input->record_08b_1;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x58bbU)=(uint8_t)input->record_08b_2;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x58bcU)=(uint8_t)input->record_08c_0;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x58bdU)=(uint8_t)input->record_08c_1;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x58beU)=(uint8_t)input->record_08c_2;

    return 1;
}
int main(void)
{
    unsigned long index;
    for(index=0;index<ARRAY_SIZE(diagnostic_record_composite_gate_cases);++index){
        const struct path_case *input=&diagnostic_record_composite_gate_cases[index];
        struct context before,context=input->context;struct observation out;
        if(!prepare(input))return 1;
        memcpy(&before,&context,sizeof(before));memset(&out,0xa6,sizeof(out));
        memcpy(memory_before,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
        snapshot(calibration_before,diagnostic_record_composite_gate_controlled,ARRAY_SIZE(diagnostic_record_composite_gate_controlled));
        snapshot(bound_before,diagnostic_record_composite_gate_bound,ARRAY_SIZE(diagnostic_record_composite_gate_bound));
        stock_invoke_ignition_consumer(input->entry,&context,&out);
        printf("kb-diagnostic-record-composite-gate-observation {\"schema\":1,\"index\":%lu,\"kind\":%lu,\"entry\":%lu,\"context\":\"",
            index,(unsigned long)input->kind,(unsigned long)input->entry);
        hex(&before,sizeof(before));printf("\",\"context_after\":\"");hex(&context,sizeof(context));
        printf("\",\"observation\":\"");hex(&out,sizeof(out));
        printf("\",\"ram_before\":\"");rle(memory_before,RAM_SIZE);
        printf("\",\"ram_after\":\"");rle((const uint8_t *)(uintptr_t)RAM_BASE,RAM_SIZE);
        printf("\",\"calibration_before\":\"");hex(calibration_before,sizeof(calibration_before));
        printf("\",\"calibration_after\":\"");print_spans(diagnostic_record_composite_gate_controlled,ARRAY_SIZE(diagnostic_record_composite_gate_controlled));
        printf("\",\"bound_before\":\"");hex(bound_before,sizeof(bound_before));
        printf("\",\"bound_after\":\"");print_spans(diagnostic_record_composite_gate_bound,ARRAY_SIZE(diagnostic_record_composite_gate_bound));
        printf("\"}\n");
    }
    printf("VQ_SH_ELF_DIAGNOSTIC_RECORD_COMPOSITE_GATE status=PASS region=%s cases=%lu\n",DIAGNOSTIC_RECORD_COMPOSITE_GATE_REGION,index);
    return 0;
}
