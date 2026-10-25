/* Complete raw timing weight controls and one full natural candidate-builder invocation. */
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
#include "second-channel-weight-cases.h"
_Static_assert(sizeof(void *)==4U,"SH-2E pointer ABI");
_Static_assert(sizeof(struct context)==80U,"complete incoming context");
_Static_assert(offsetof(struct context,fifth)==76U,"ordinary stack argument");
_Static_assert(sizeof(struct observation)==572U,"unchanged ordinary observer");
_Static_assert(offsetof(struct observation,frame_before)==184U,"complete entry frame");
_Static_assert(offsetof(struct observation,frame_after)==376U,"complete exit frame");
_Static_assert(offsetof(struct observation,sr_before)==568U,"complete SR input");
extern void stock_invoke_ignition_consumer(uint32_t,const struct context *,struct observation *);
static uint8_t memory_before[RAM_SIZE];
static uint8_t calibration_before[WEIGHT_CALIBRATION_SIZE],bound_before[WEIGHT_BOUND_SIZE];

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
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x249FU)=(uint8_t)input->byte_249f;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x2698U)=(uint16_t)input->word_2698;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x2C71U)=(uint8_t)input->byte_2c71;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x10BCU)=(uint16_t)input->word_10bc;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x245EU)=(uint8_t)input->byte_245e;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x31E2U)=(uint16_t)input->word_31e2;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x3024U)=(uint16_t)input->word_3024;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x4214U)=(uint8_t)input->byte_4214;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x35EAU)=(uint16_t)input->word_35ea;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x35F4U)=(uint16_t)input->prior_35f4;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x35CAU)=(uint16_t)input->prior_35ca;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x35FCU)=(uint16_t)input->prior_35fc;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x35CCU)=(uint16_t)input->prior_35cc;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x1248U)=(uint16_t)input->prior_1248;
    *(volatile uint32_t *)(uintptr_t)(RAM_BASE+0x9818U)=(uint32_t)input->prior_9818;
    for(i=0;i<ARRAY_SIZE(weight_calibration);++i){
        memcpy((void *)(uintptr_t)weight_calibration[i].address,input->calibration+offset,weight_calibration[i].size);
        offset+=weight_calibration[i].size;
    }
}

int main(void)
{
    size_t index;
    for(index=0;index<ARRAY_SIZE(weight_cases);++index){
        const struct path_case *input=&weight_cases[index];
        struct context before,context=input->context;struct observation out;
        prepare(input);before=context;memset(&out,0xA6,sizeof(out));
        memcpy(memory_before,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
        snapshot(calibration_before,weight_calibration,ARRAY_SIZE(weight_calibration));
        snapshot(bound_before,weight_bound,ARRAY_SIZE(weight_bound));
        stock_invoke_ignition_consumer(0x7A804U,&context,&out);
        printf("kb-second-channel-weight-observation {\"schema\":1,\"index\":%lu,\"entry\":%lu,\"context\":\"",
            (unsigned long)index,(unsigned long)0x7A804U);
        hex(&before,sizeof(before));printf("\",\"context_after\":\"");hex(&context,sizeof(context));
        printf("\",\"observation\":\"");hex(&out,sizeof(out));
        printf("\",\"ram_before\":\"");rle(memory_before,RAM_SIZE);
        printf("\",\"ram_after\":\"");rle((const uint8_t *)(uintptr_t)RAM_BASE,RAM_SIZE);
        printf("\",\"calibration_before\":\"");hex(calibration_before,sizeof(calibration_before));
        printf("\",\"calibration_after\":\"");print_spans(weight_calibration,ARRAY_SIZE(weight_calibration));
        printf("\",\"bound_before\":\"");hex(bound_before,sizeof(bound_before));
        printf("\",\"bound_after\":\"");print_spans(weight_bound,ARRAY_SIZE(weight_bound));printf("\"}\n");
    }
    printf("VQ_SH_ELF_SECOND_CHANNEL_WEIGHT status=PASS region=jk08a-second-channel-weight-paths cases=%lu\n",
        (unsigned long)index);return 0;
}
