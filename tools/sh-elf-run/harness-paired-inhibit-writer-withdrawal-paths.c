/* Input driver defined by defs/JK08A.paired-inhibit-writer-withdrawal-paths.toml. */
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
#include "paired-inhibit-writer-withdrawal-cases.h"
_Static_assert(sizeof(void *)==4U,"SH-2E pointer ABI");
_Static_assert(sizeof(struct context)==80U,"complete incoming context");
_Static_assert(offsetof(struct context,fifth)==76U,"existing observer stack argument");
_Static_assert(sizeof(struct observation)==572U,"complete observer result");
_Static_assert(offsetof(struct observation,frame_before)==184U,"complete incoming frame");
_Static_assert(offsetof(struct observation,frame_after)==376U,"complete terminal frame");
_Static_assert(offsetof(struct observation,sr_before)==568U,"complete prepared SR");
extern void stock_invoke_ignition_consumer(uint32_t,const struct context *,struct observation *);
static uint8_t memory_before[RAM_SIZE],calibration_before[PAIRED_INHIBIT_WRITER_WITHDRAWAL_CALIBRATION_SIZE];
static uint8_t bound_before[PAIRED_INHIBIT_WRITER_WITHDRAWAL_BOUND_SIZE];
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
    if((input->entry!=0x7c8faU && input->entry!=0x7c9a8U) || input->kind>=2U || input->byte_3118>0xffU || input->byte_41bb>0xffU || input->byte_41c1>0xffU || input->byte_41c5>0xffU || input->byte_41cf>0xffU || input->byte_41d4>0xffU || input->byte_41d8>0xffU || input->byte_48c2>0xffU || input->byte_48c4>0xffU || input->byte_4a45>0xffU || input->byte_4a47>0xffU || input->word_4a70>0xffffU || input->word_4a74>0xffffU || input->byte_4ac6>0xffU || input->byte_4ac8>0xffU || input->byte_5737>0xffU || input->byte_5738>0xffU || input->byte_573a>0xffU || input->byte_573b>0xffU || input->byte_573d>0xffU || input->byte_573e>0xffU || input->byte_5740>0xffU || input->byte_5741>0xffU || input->byte_5743>0xffU || input->byte_5744>0xffU || input->byte_5746>0xffU || input->byte_5747>0xffU || input->byte_5749>0xffU || input->byte_574a>0xffU || input->byte_5b2a>0xffU || input->byte_5b2b>0xffU || input->byte_5b2c>0xffU || input->byte_5b33>0xffU || input->config_885d>0xffU || input->variant>0xffU || input->initial_sr>0x3ffU)return 0;
    memset((void *)(uintptr_t)RAM_BASE,0xa5,RAM_SIZE);
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x3118U)=(uint8_t)input->byte_3118;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x41bbU)=(uint8_t)input->byte_41bb;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x41c1U)=(uint8_t)input->byte_41c1;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x41c5U)=(uint8_t)input->byte_41c5;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x41cfU)=(uint8_t)input->byte_41cf;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x41d4U)=(uint8_t)input->byte_41d4;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x41d8U)=(uint8_t)input->byte_41d8;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x48c2U)=(uint8_t)input->byte_48c2;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x48c4U)=(uint8_t)input->byte_48c4;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x4a45U)=(uint8_t)input->byte_4a45;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x4a47U)=(uint8_t)input->byte_4a47;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x4a70U)=(uint16_t)input->word_4a70;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x4a74U)=(uint16_t)input->word_4a74;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x4ac6U)=(uint8_t)input->byte_4ac6;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x4ac8U)=(uint8_t)input->byte_4ac8;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x5737U)=(uint8_t)input->byte_5737;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x5738U)=(uint8_t)input->byte_5738;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x573aU)=(uint8_t)input->byte_573a;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x573bU)=(uint8_t)input->byte_573b;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x573dU)=(uint8_t)input->byte_573d;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x573eU)=(uint8_t)input->byte_573e;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x5740U)=(uint8_t)input->byte_5740;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x5741U)=(uint8_t)input->byte_5741;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x5743U)=(uint8_t)input->byte_5743;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x5744U)=(uint8_t)input->byte_5744;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x5746U)=(uint8_t)input->byte_5746;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x5747U)=(uint8_t)input->byte_5747;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x5749U)=(uint8_t)input->byte_5749;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x574aU)=(uint8_t)input->byte_574a;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x5b2aU)=(uint8_t)input->byte_5b2a;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x5b2bU)=(uint8_t)input->byte_5b2b;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x5b2cU)=(uint8_t)input->byte_5b2c;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x5b33U)=(uint8_t)input->byte_5b33;
    for(index=0;index<ARRAY_SIZE(paired_inhibit_writer_withdrawal_controlled);++index){
        memcpy((void *)(uintptr_t)paired_inhibit_writer_withdrawal_controlled[index].address,input->calibration+offset,
            paired_inhibit_writer_withdrawal_controlled[index].size);
        offset+=paired_inhibit_writer_withdrawal_controlled[index].size;
    }
    if(offset!=PAIRED_INHIBIT_WRITER_WITHDRAWAL_CALIBRATION_SIZE)return 0;
    return 1;
}
int main(void)
{
    unsigned long index;
    for(index=0;index<ARRAY_SIZE(paired_inhibit_writer_withdrawal_cases);++index){
        const struct path_case *input=&paired_inhibit_writer_withdrawal_cases[index];
        struct context before,context=input->context;struct observation out;
        if(!prepare(input))return 1;
        memcpy(&before,&context,sizeof(before));memset(&out,0xa6,sizeof(out));
        memcpy(memory_before,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
        snapshot(calibration_before,paired_inhibit_writer_withdrawal_controlled,ARRAY_SIZE(paired_inhibit_writer_withdrawal_controlled));
        snapshot(bound_before,paired_inhibit_writer_withdrawal_bound,ARRAY_SIZE(paired_inhibit_writer_withdrawal_bound));
        stock_invoke_ignition_consumer(input->entry,&context,&out);
        printf("kb-paired-inhibit-writer-withdrawal-observation {\"schema\":1,\"index\":%lu,\"kind\":%lu,\"entry\":%lu,\"context\":\"",
            index,(unsigned long)input->kind,(unsigned long)input->entry);
        hex(&before,sizeof(before));printf("\",\"context_after\":\"");hex(&context,sizeof(context));
        printf("\",\"observation\":\"");hex(&out,sizeof(out));
        printf("\",\"ram_before\":\"");rle(memory_before,RAM_SIZE);
        printf("\",\"ram_after\":\"");rle((const uint8_t *)(uintptr_t)RAM_BASE,RAM_SIZE);
        printf("\",\"calibration_before\":\"");hex(calibration_before,sizeof(calibration_before));
        printf("\",\"calibration_after\":\"");print_spans(paired_inhibit_writer_withdrawal_controlled,ARRAY_SIZE(paired_inhibit_writer_withdrawal_controlled));
        printf("\",\"bound_before\":\"");hex(bound_before,sizeof(bound_before));
        printf("\",\"bound_after\":\"");print_spans(paired_inhibit_writer_withdrawal_bound,ARRAY_SIZE(paired_inhibit_writer_withdrawal_bound));
        printf("\"}\n");
    }
    printf("VQ_SH_ELF_DFCO_STATE_CALLER_WITHDRAWAL status=PASS region=%s cases=%lu\n",PAIRED_INHIBIT_WRITER_WITHDRAWAL_REGION,index);
    return 0;
}
