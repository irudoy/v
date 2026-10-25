/* Input-only whole feedback execution with complete unclassified observations. */
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>

#define RAM_BASE 0x01000000U
#define RAM_SIZE 65536U
#define WORK_BASE 0x00005ffcU
#define WORK_SIZE 302U
#define WORK_OBSERVED 366U
#define COUNT(value) (sizeof(value)/sizeof((value)[0]))
struct context { uint32_t r[15],gbr,mach,macl,entry_sr; };
struct observation {
    uint32_t exit[20],sp,continuation,abi_before[12],abi_after[12];
    uint8_t frame_before[352],frame_after[352];uint32_t sr_before;
};
struct change { uint32_t offset,value; };
struct span { uint32_t at,size; };
struct path_case {
    uint32_t kind,entry,zero,seed_index,input_begin,input_count;
    struct context context;uint8_t calibration[18];
};
#include "closed-loop-feedback-path-cases.h"
_Static_assert(sizeof(void *)==4U,"SH-2E pointer ABI");
_Static_assert(sizeof(struct context)==76U,"existing complete feedback input context");
_Static_assert(sizeof(struct observation)==892U,"existing complete feedback observer");
_Static_assert(offsetof(struct observation,frame_before)==184U,"existing feedback frame offset");
_Static_assert(offsetof(struct observation,frame_after)==536U,"existing feedback terminal frame offset");
_Static_assert(offsetof(struct observation,sr_before)==888U,"existing full prepared SR offset");
extern void stock_invoke_closed_loop_feedback(uint32_t,const struct context *,struct observation *);
static uint8_t ram_before[RAM_SIZE],workspace_before[WORK_OBSERVED];
static uint8_t bound_before[FEEDBACK_BOUND_SIZE],bound_after[FEEDBACK_BOUND_SIZE];
static uint8_t calibration_before[18];

static void hex(const void *pointer,size_t size)
{
    const uint8_t *data=pointer;size_t index;
    for (index=0;index<size;++index) printf("%02x",(unsigned)data[index]);
}
static void rle(const uint8_t *data,size_t size)
{
    size_t start=0;
    while (start<size) {
        size_t end=start+1U;
        while (end<size && data[end]==data[start]) ++end;
        printf("%s%lu:%02x",start ? "," : "",(unsigned long)(end-start),(unsigned)data[start]);
        start=end;
    }
}
static void snapshot_bound(uint8_t *destination)
{
    unsigned index,offset=0;
    for (index=0;index<COUNT(feedback_bound);++index) {
        memcpy(destination+offset,(const void *)(uintptr_t)feedback_bound[index].at,feedback_bound[index].size);
        offset+=feedback_bound[index].size;
    }
}
static void snapshot_calibration(uint8_t *destination)
{
    unsigned index,offset=0;
    for (index=0;index<COUNT(feedback_controlled);++index) {
        memcpy(destination+offset,(const void *)(uintptr_t)feedback_controlled[index].at,feedback_controlled[index].size);
        offset+=feedback_controlled[index].size;
    }
}
static int prepare(const struct path_case *input)
{
    unsigned index,offset=0;volatile uint8_t *ram=(volatile uint8_t *)(uintptr_t)RAM_BASE;
    volatile uint8_t *native=(volatile uint8_t *)(uintptr_t)(WORK_BASE-32U);
    if (input->entry!=0x5cbecU || input->kind>1U || input->zero>1U) return 0;
    for (index=0;index<RAM_SIZE;++index)
        ram[index]=input->zero ? 0U : (uint8_t)(0x51U+29U*index+(index>>8)+input->seed_index);
    for (index=0;index<input->input_count;++index) {
        const struct change *change=&feedback_changes[input->input_begin+index];
        if (change->offset>=RAM_SIZE || change->value>255U) return 0;
        ram[change->offset]=(uint8_t)change->value;
    }
    for (index=0;index<WORK_OBSERVED;++index) native[index]=(uint8_t)(0x91U+13U*index+input->seed_index);
    memcpy((void *)(uintptr_t)WORK_BASE,(const void *)(uintptr_t)(RAM_BASE+0x88b0U),WORK_SIZE);
    for (index=0;index<COUNT(feedback_controlled);++index) {
        memcpy((void *)(uintptr_t)feedback_controlled[index].at,input->calibration+offset,feedback_controlled[index].size);
        offset+=feedback_controlled[index].size;
    }
    return 1;
}
static int observe(size_t index)
{
    const struct path_case *input=&feedback_cases[index];
    struct context context=input->context,initial=context;
    struct observation observation;uint8_t calibration_after[18];
    if (!prepare(input)) return 0;
    memcpy(ram_before,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
    memcpy(workspace_before,(const void *)(uintptr_t)(WORK_BASE-32U),WORK_OBSERVED);
    snapshot_bound(bound_before);snapshot_calibration(calibration_before);
    memset(&observation,0xa6,sizeof(observation));
    stock_invoke_closed_loop_feedback(input->entry,&context,&observation);
    snapshot_bound(bound_after);snapshot_calibration(calibration_after);
    printf("kb-closed-loop-feedback-observation {\"schema\":1,\"index\":%lu,\"kind\":%lu,\"entry\":%lu,\"context\":\"",
        (unsigned long)index,(unsigned long)input->kind,(unsigned long)input->entry);
    hex(&initial,sizeof(initial));printf("\",\"context_after\":\"");hex(&context,sizeof(context));
    printf("\",\"observation\":\"");hex(&observation,sizeof(observation));
    printf("\",\"ram_before\":\"");rle(ram_before,RAM_SIZE);
    printf("\",\"ram_after\":\"");rle((const uint8_t *)(uintptr_t)RAM_BASE,RAM_SIZE);
    printf("\",\"workspace_before\":\"");hex(workspace_before,WORK_OBSERVED);
    printf("\",\"workspace_after\":\"");hex((const void *)(uintptr_t)(WORK_BASE-32U),WORK_OBSERVED);
    printf("\",\"calibration_before\":\"");hex(calibration_before,sizeof(calibration_before));
    printf("\",\"calibration_after\":\"");hex(calibration_after,sizeof(calibration_after));
    printf("\",\"bound_before\":\"");rle(bound_before,FEEDBACK_BOUND_SIZE);
    printf("\",\"bound_after\":\"");rle(bound_after,FEEDBACK_BOUND_SIZE);printf("\"}\n");
    return 1;
}
int main(void)
{
    size_t index;
    for (index=0;index<COUNT(feedback_cases);++index) if (!observe(index)) return 1;
    printf("VQ_SH_ELF_CLOSED_LOOP_FEEDBACK status=PASS region=%s cases=%lu\n",
        FEEDBACK_REGION,(unsigned long)COUNT(feedback_cases));
    return 0;
}
