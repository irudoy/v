/* Input driver defined by defs/JK08A.scalar-ram-leaves.toml. */
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
#include "scalar-ram-leaf-cases.h"
_Static_assert(sizeof(void *)==4U,"SH-2E pointer ABI");
_Static_assert(sizeof(struct context)==80U,"complete incoming context");
_Static_assert(offsetof(struct context,fifth)==76U,"existing observer stack argument");
_Static_assert(sizeof(struct observation)==572U,"complete observer result");
_Static_assert(offsetof(struct observation,frame_before)==184U,"complete incoming frame");
_Static_assert(offsetof(struct observation,frame_after)==376U,"complete terminal frame");
_Static_assert(offsetof(struct observation,sr_before)==568U,"complete prepared SR");
extern void stock_invoke_ignition_consumer(uint32_t,const struct context *,struct observation *);
static uint8_t memory_before[RAM_SIZE],calibration_before[SCALAR_RAM_LEAVES_CALIBRATION_SIZE];
static uint8_t bound_before[SCALAR_RAM_LEAVES_BOUND_SIZE];
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
    if((input->entry!=0x259beU && input->entry!=0x39588U && input->entry!=0x39874U && input->entry!=0x468b0U && input->entry!=0x4ab94U && input->entry!=0x4af38U && input->entry!=0x4bb6aU && input->entry!=0x4c136U && input->entry!=0x4e112U && input->entry!=0x554aeU && input->entry!=0x70d82U && input->entry!=0xa5530U) || input->kind>=12U || input->slew_a_current>0xffU || input->slew_a_target>0xffU || input->slew_b_current>0xffU || input->slew_b_target>0xffU || input->sum_word_a>0xffffU || input->sum_byte_a>0xffU || input->sum_word_b>0xffffU || input->sum_signed_a>0xffffU || input->sum_byte_b>0xffU || input->sum_byte_c>0xffU || input->sum_signed_b>0xffffU || input->sum_optional>0xffU || input->state_231a>0xffffU || input->word_230c>0xffffU || input->product_gain>0xffffU || input->timing_first>0xffU || input->timing_second>0xffU || input->timing_offset>0xffU || input->combine_first>0xffU || input->combine_second>0xffU || input->combine_trim>0xffU || input->latch_flags>0xffU || input->latch_flag_state>0xffU || input->latch_mode>0xffU || input->latch_status>0xffU || input->latch_primary>0xffU || input->latch_alternate>0xffU || input->decay_flags>0xffU || input->decay_latched>0xffU || input->decay_state>0xffU || input->accumulator_correction>0xffffU || input->selector_flags>0xffU || input->selector_state>0xffU || input->selector_candidate>0xffffU || input->selector_primary>0xffffU || input->limit_flags>0xffU || input->limit_gate>0xffU || input->limit_current>0xffffU || input->limit_threshold>0xffffU || input->sum_configuration>0xffU || input->timing_configuration>0xffU || input->decay_configuration>0xffU || input->variant>0xffU || input->initial_sr>0x3ffU)return 0;
    memset((void *)(uintptr_t)RAM_BASE,0xa5,RAM_SIZE);
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1187U)=(uint8_t)input->slew_a_current;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1081U)=(uint8_t)input->slew_a_target;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1f89U)=(uint8_t)input->slew_b_current;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x107cU)=(uint8_t)input->slew_b_target;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x1752U)=(uint16_t)input->sum_word_a;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1765U)=(uint8_t)input->sum_byte_a;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x1748U)=(uint16_t)input->sum_word_b;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x1230U)=(uint16_t)input->sum_signed_a;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x15acU)=(uint8_t)input->sum_byte_b;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x13f7U)=(uint8_t)input->sum_byte_c;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x170aU)=(uint16_t)input->sum_signed_b;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1f62U)=(uint8_t)input->sum_optional;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x231aU)=(uint16_t)input->state_231a;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x230cU)=(uint16_t)input->word_230c;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x22e8U)=(uint16_t)input->product_gain;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x160fU)=(uint8_t)input->timing_first;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1610U)=(uint8_t)input->timing_second;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x11afU)=(uint8_t)input->timing_offset;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x22feU)=(uint8_t)input->combine_first;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x22f8U)=(uint8_t)input->combine_second;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1657U)=(uint8_t)input->combine_trim;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x4184U)=(uint8_t)input->latch_flags;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x24d2U)=(uint8_t)input->latch_flag_state;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1239U)=(uint8_t)input->latch_mode;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x2458U)=(uint8_t)input->latch_status;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1830U)=(uint8_t)input->latch_primary;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1831U)=(uint8_t)input->latch_alternate;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x248dU)=(uint8_t)input->decay_flags;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x25fdU)=(uint8_t)input->decay_latched;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1513U)=(uint8_t)input->decay_state;
    *(volatile uint32_t *)(uintptr_t)(RAM_BASE+0x15f8U)=(uint32_t)input->accumulator_delta;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x15daU)=(uint16_t)input->accumulator_correction;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x2490U)=(uint8_t)input->selector_flags;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x25d6U)=(uint8_t)input->selector_state;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x19c0U)=(uint16_t)input->selector_candidate;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x243aU)=(uint16_t)input->selector_primary;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x4204U)=(uint8_t)input->limit_flags;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x244fU)=(uint8_t)input->limit_gate;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x3334U)=(uint16_t)input->limit_current;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x32eeU)=(uint16_t)input->limit_threshold;
    for(index=0;index<ARRAY_SIZE(scalar_ram_leaves_controlled);++index){
        memcpy((void *)(uintptr_t)scalar_ram_leaves_controlled[index].address,input->calibration+offset,
            scalar_ram_leaves_controlled[index].size);
        offset+=scalar_ram_leaves_controlled[index].size;
    }
    if(offset!=SCALAR_RAM_LEAVES_CALIBRATION_SIZE)return 0;
    return 1;
}
int main(void)
{
    unsigned long index;
    for(index=0;index<ARRAY_SIZE(scalar_ram_leaves_cases);++index){
        const struct path_case *input=&scalar_ram_leaves_cases[index];
        struct context before,context=input->context;struct observation out;
        if(!prepare(input))return 1;
        memcpy(&before,&context,sizeof(before));memset(&out,0xa6,sizeof(out));
        memcpy(memory_before,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
        snapshot(calibration_before,scalar_ram_leaves_controlled,ARRAY_SIZE(scalar_ram_leaves_controlled));
        snapshot(bound_before,scalar_ram_leaves_bound,ARRAY_SIZE(scalar_ram_leaves_bound));
        stock_invoke_ignition_consumer(input->entry,&context,&out);
        printf("kb-scalar-ram-leaf-observation {\"schema\":1,\"index\":%lu,\"kind\":%lu,\"entry\":%lu,\"context\":\"",
            index,(unsigned long)input->kind,(unsigned long)input->entry);
        hex(&before,sizeof(before));printf("\",\"context_after\":\"");hex(&context,sizeof(context));
        printf("\",\"observation\":\"");hex(&out,sizeof(out));
        printf("\",\"ram_before\":\"");rle(memory_before,RAM_SIZE);
        printf("\",\"ram_after\":\"");rle((const uint8_t *)(uintptr_t)RAM_BASE,RAM_SIZE);
        printf("\",\"calibration_before\":\"");hex(calibration_before,sizeof(calibration_before));
        printf("\",\"calibration_after\":\"");print_spans(scalar_ram_leaves_controlled,ARRAY_SIZE(scalar_ram_leaves_controlled));
        printf("\",\"bound_before\":\"");hex(bound_before,sizeof(bound_before));
        printf("\",\"bound_after\":\"");print_spans(scalar_ram_leaves_bound,ARRAY_SIZE(scalar_ram_leaves_bound));
        printf("\"}\n");
    }
    printf("VQ_SH_ELF_SCALAR_RAM_LEAVES status=PASS region=%s cases=%lu\n",SCALAR_RAM_LEAVES_REGION,index);
    return 0;
}
