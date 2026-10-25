/* Complete input state and one natural stock native index1 learned-trim adjustment invocation. */
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
#include "ltft-adjustment-update-cases.h"
_Static_assert(sizeof(void *)==4U,"SH-2E pointer ABI");
_Static_assert(sizeof(struct context)==80U,"complete incoming context");
_Static_assert(offsetof(struct context,fifth)==76U,"ordinary stack argument");
_Static_assert(sizeof(struct observation)==572U,"unchanged ordinary observer");
_Static_assert(offsetof(struct observation,frame_before)==184U,"complete entry frame");
_Static_assert(offsetof(struct observation,frame_after)==376U,"complete exit frame");
_Static_assert(offsetof(struct observation,sr_before)==568U,"complete SR input");
extern void stock_invoke_ignition_consumer(uint32_t,const struct context *,struct observation *);
static uint8_t memory_before[RAM_SIZE];
static uint8_t calibration_before[TRIM_CALIBRATION_SIZE],bound_before[TRIM_BOUND_SIZE];

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
    size_t i,j,offset=0;
    memset((void *)(uintptr_t)RAM_BASE,input->pattern,RAM_SIZE);
    for(i=0;i<ARRAY_SIZE(trim_ram_fields);++i){
        const struct span *field=&trim_ram_fields[i];
        volatile uint8_t *target=(volatile uint8_t *)(uintptr_t)(RAM_BASE+field->address);
        for(j=0;j<field->size;++j)target[j]=(uint8_t)(input->ram[i]>>(8U*(field->size-j-1U)));
    }
    for(i=0;i<ARRAY_SIZE(trim_calibration);++i){
        memcpy((void *)(uintptr_t)trim_calibration[i].address,trim_calibration_blobs[input->calibration_index]+offset,trim_calibration[i].size);
        offset+=trim_calibration[i].size;
    }
}
int main(void)
{
    size_t index;
    for(index=0;index<ARRAY_SIZE(trim_cases);++index){
        const struct path_case *input=&trim_cases[index];
        struct context before,context=input->context;struct observation out;
        prepare(input);before=context;memset(&out,0xA6,sizeof(out));
        memcpy(memory_before,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
        snapshot(calibration_before,trim_calibration,ARRAY_SIZE(trim_calibration));
        snapshot(bound_before,trim_bound,ARRAY_SIZE(trim_bound));
        stock_invoke_ignition_consumer(0x58168U,&context,&out);
        printf("kb-ltft-adjustment-update-observation {\"schema\":1,\"index\":%lu,\"entry\":%lu,\"context\":\"",
            (unsigned long)index,(unsigned long)0x58168U);
        hex(&before,sizeof(before));printf("\",\"context_after\":\"");hex(&context,sizeof(context));
        printf("\",\"observation\":\"");hex(&out,sizeof(out));
        printf("\",\"ram_before\":\"");rle(memory_before,RAM_SIZE);
        printf("\",\"ram_after\":\"");rle((const uint8_t *)(uintptr_t)RAM_BASE,RAM_SIZE);
        printf("\",\"calibration_before\":\"");hex(calibration_before,sizeof(calibration_before));
        printf("\",\"calibration_after\":\"");print_spans(trim_calibration,ARRAY_SIZE(trim_calibration));
        printf("\",\"bound_before\":\"");hex(bound_before,sizeof(bound_before));
        printf("\",\"bound_after\":\"");print_spans(trim_bound,ARRAY_SIZE(trim_bound));printf("\"}\n");
    }
    printf("VQ_SH_ELF_LTFT_ADJUSTMENT_UPDATE status=PASS region=jk08a-ltft-adjustment-update-paths cases=%lu\n",
        (unsigned long)index);return 0;
}
