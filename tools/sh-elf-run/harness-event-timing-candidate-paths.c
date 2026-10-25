/* Complete raw event timing controls and one full natural candidate-builder invocation. */
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#define RAM_BASE 0x01000000U
#define RAM_SIZE 65536U
#define ARRAY_SIZE(v) (sizeof(v)/sizeof((v)[0]))
struct context { uint32_t r[15],gbr,mach,macl,entry_sr,fifth; };
struct observation {
    uint32_t exit[20],sp,continuation,abi_before[12],abi_after[12];
    uint8_t frame_before[192],frame_after[192];uint32_t sr_before;
};
struct span { uint32_t address,size; };
#include "event-timing-candidate-cases.h"
_Static_assert(sizeof(void *)==4U,"SH-2E pointer ABI");
_Static_assert(sizeof(struct context)==80U,"complete incoming context");
_Static_assert(offsetof(struct context,fifth)==76U,"ordinary stack argument");
_Static_assert(sizeof(struct observation)==572U,"unchanged ordinary observer");
_Static_assert(offsetof(struct observation,frame_before)==184U,"complete entry frame");
_Static_assert(offsetof(struct observation,frame_after)==376U,"complete exit frame");
_Static_assert(offsetof(struct observation,sr_before)==568U,"complete SR input");
extern void stock_invoke_ignition_consumer(uint32_t,const struct context *,struct observation *);
static uint8_t memory_before[RAM_SIZE];
static uint8_t calibration_before[EVENT_CALIBRATION_SIZE],bound_before[EVENT_BOUND_SIZE];

static void hex(const void *pointer,size_t size)
{
    const uint8_t *data=pointer;size_t n;
    for(n=0;n<size;++n)printf("%02x",(unsigned)data[n]);
}
static void rle(const uint8_t *data,size_t size)
{
    size_t start=0;
    while(start<size){size_t end=start+1U;while(end<size&&data[start]==data[end])++end;
        printf("%s%lu:%02x",start?",":"",(unsigned long)(end-start),(unsigned)data[start]);start=end;}
}
static void snapshot(uint8_t *output,const struct span *spans,size_t count)
{
    size_t i,offset=0;
    for(i=0;i<count;++i){memcpy(output+offset,(const void *)(uintptr_t)spans[i].address,spans[i].size);offset+=spans[i].size;}
}
static void print_spans(const struct span *spans,size_t count)
{
    size_t i;
    for(i=0;i<count;++i)hex((const void *)(uintptr_t)spans[i].address,spans[i].size);
}
static void prepare(const struct path_case *input)
{
    size_t i,offset=0;
    memset((void *)(uintptr_t)RAM_BASE,input->pattern,RAM_SIZE);
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x24C5U)=(uint8_t)input->byte_24c5;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x24CBU)=(uint8_t)input->byte_24cb;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x11F9U)=(uint8_t)input->byte_11f9;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x11FAU)=(uint8_t)input->byte_11fa;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x23C2U)=(uint16_t)input->word_23c2;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x22FAU)=(uint8_t)input->byte_22fa;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x24CCU)=(uint8_t)input->byte_24cc;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x24C2U)=(uint8_t)input->byte_24c2;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x2378U)=(uint8_t)input->byte_2378;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x24C0U)=(uint8_t)input->byte_24c0;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x229DU)=(uint8_t)input->byte_229d;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x25FCU)=(uint8_t)input->byte_25fc;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x237EU)=(uint16_t)input->word_237e;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x2459U)=(uint8_t)input->byte_2459;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x40E7U)=(uint8_t)input->byte_40e7;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x2356U)=(uint8_t)input->byte_2356;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x11D6U)=(uint16_t)input->prior_11d6;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x11D8U)=(uint16_t)input->prior_11d8;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x2000U)=(uint16_t)input->prior_2000;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x1FF6U)=(uint16_t)input->prior_1ff6;
    *(volatile uint32_t *)(uintptr_t)(RAM_BASE+0x1FF8U)=(uint32_t)input->prior_1ff8;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x226CU)=(uint8_t)input->prior_226c;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x12D6U)=(uint8_t)input->prior_12d6;
    *(volatile uint32_t *)(uintptr_t)(RAM_BASE+0x9818U)=(uint32_t)input->prior_9818;
    for(i=0;i<ARRAY_SIZE(event_calibration);++i){
        memcpy((void *)(uintptr_t)event_calibration[i].address,input->calibration+offset,event_calibration[i].size);
        offset+=event_calibration[i].size;
    }
}

int main(void)
{
    size_t index;
    for(index=0;index<ARRAY_SIZE(event_cases);++index){
        const struct path_case *input=&event_cases[index];
        struct context before,context=input->context;struct observation out;
        prepare(input);before=context;memset(&out,0xA6,sizeof(out));
        memcpy(memory_before,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
        snapshot(calibration_before,event_calibration,ARRAY_SIZE(event_calibration));
        snapshot(bound_before,event_bound,ARRAY_SIZE(event_bound));
        stock_invoke_ignition_consumer(0x4D99CU,&context,&out);
        printf("kb-event-timing-candidate-observation {\"schema\":1,\"index\":%lu,\"entry\":%lu,\"context\":\"",
            (unsigned long)index,(unsigned long)0x4D99CU);
        hex(&before,sizeof(before));printf("\",\"context_after\":\"");hex(&context,sizeof(context));
        printf("\",\"observation\":\"");hex(&out,sizeof(out));
        printf("\",\"ram_before\":\"");rle(memory_before,RAM_SIZE);
        printf("\",\"ram_after\":\"");rle((const uint8_t *)(uintptr_t)RAM_BASE,RAM_SIZE);
        printf("\",\"calibration_before\":\"");hex(calibration_before,sizeof(calibration_before));
        printf("\",\"calibration_after\":\"");print_spans(event_calibration,ARRAY_SIZE(event_calibration));
        printf("\",\"bound_before\":\"");hex(bound_before,sizeof(bound_before));
        printf("\",\"bound_after\":\"");print_spans(event_bound,ARRAY_SIZE(event_bound));printf("\"}\n");
    }
    printf("VQ_SH_ELF_EVENT_TIMING_CANDIDATE status=PASS region=jk08a-event-timing-candidate-paths cases=%lu\n",
        (unsigned long)index);return 0;
}
