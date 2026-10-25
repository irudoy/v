/* Input driver defined by defs/JK08A.closed-loop-coolant-accesses.toml. */
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
#include "closed-loop-coolant-path-cases.h"
_Static_assert(sizeof(void *)==4U,"SH-2E pointer ABI");
_Static_assert(sizeof(struct context)==80U,"complete incoming context");
_Static_assert(offsetof(struct context,fifth)==76U,"existing observer stack argument");
_Static_assert(sizeof(struct observation)==572U,"complete observer result");
_Static_assert(offsetof(struct observation,frame_before)==184U,"complete incoming frame");
_Static_assert(offsetof(struct observation,frame_after)==376U,"complete terminal frame");
_Static_assert(offsetof(struct observation,sr_before)==568U,"complete prepared SR");
extern void stock_invoke_ignition_consumer(uint32_t,const struct context *,struct observation *);
static uint8_t memory_before[RAM_SIZE],calibration_before[COOLANT_CALIBRATION_SIZE];
static uint8_t bound_before[COOLANT_BOUND_SIZE];
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
    if((input->entry!=0x5525aU) || input->kind>=2U || input->rpm>0xffU || input->warm>0xffU || input->previous_coolant>0xffU || input->load>0xffU || input->rpm_select>0xffU || input->flags_a>0xffU || input->flags_b>0xffU || input->source_flag>0xffU || input->direction_flag>0xffU || input->old>0xffffU || input->mixture>0xffffU || input->hysteresis>0xffU || input->rate>0xffffU || input->cap>0xffffU || input->coolant_offset>0xffffU || input->variant>0x1U)return 0;
    memset((void *)(uintptr_t)RAM_BASE,0xa5,RAM_SIZE);
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x11b3U)=(uint8_t)input->rpm;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1107U)=(uint8_t)input->warm;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x106fU)=(uint8_t)input->previous_coolant;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x102cU)=(uint8_t)input->load;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x11aeU)=(uint8_t)input->rpm_select;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x2492U)=(uint8_t)input->flags_a;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x2493U)=(uint8_t)input->flags_b;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x2458U)=(uint8_t)input->source_flag;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x2485U)=(uint8_t)input->direction_flag;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x15daU)=(uint16_t)input->old;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x22e8U)=(uint16_t)input->mixture;
    for(index=0;index<ARRAY_SIZE(coolant_controlled);++index){
        memcpy((void *)(uintptr_t)coolant_controlled[index].address,input->calibration+offset,
            coolant_controlled[index].size);
        offset+=coolant_controlled[index].size;
    }
    if(offset!=COOLANT_CALIBRATION_SIZE)return 0;
    return 1;
}
int main(void)
{
    unsigned long index;
    for(index=0;index<ARRAY_SIZE(coolant_cases);++index){
        const struct path_case *input=&coolant_cases[index];
        struct context before,context=input->context;struct observation out;
        if(!prepare(input))return 1;
        memcpy(&before,&context,sizeof(before));memset(&out,0xa6,sizeof(out));
        memcpy(memory_before,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
        snapshot(calibration_before,coolant_controlled,ARRAY_SIZE(coolant_controlled));
        snapshot(bound_before,coolant_bound,ARRAY_SIZE(coolant_bound));
        stock_invoke_ignition_consumer(input->entry,&context,&out);
        printf("kb-closed-loop-coolant-observation {\"schema\":1,\"index\":%lu,\"kind\":%lu,\"entry\":%lu,\"context\":\"",
            index,(unsigned long)input->kind,(unsigned long)input->entry);
        hex(&before,sizeof(before));printf("\",\"context_after\":\"");hex(&context,sizeof(context));
        printf("\",\"observation\":\"");hex(&out,sizeof(out));
        printf("\",\"ram_before\":\"");rle(memory_before,RAM_SIZE);
        printf("\",\"ram_after\":\"");rle((const uint8_t *)(uintptr_t)RAM_BASE,RAM_SIZE);
        printf("\",\"calibration_before\":\"");hex(calibration_before,sizeof(calibration_before));
        printf("\",\"calibration_after\":\"");print_spans(coolant_controlled,ARRAY_SIZE(coolant_controlled));
        printf("\",\"bound_before\":\"");hex(bound_before,sizeof(bound_before));
        printf("\",\"bound_after\":\"");print_spans(coolant_bound,ARRAY_SIZE(coolant_bound));
        printf("\"}\n");
    }
    printf("VQ_SH_ELF_CLOSED_LOOP_COOLANT status=PASS region=%s cases=%lu\n",COOLANT_REGION,index);
    return 0;
}
